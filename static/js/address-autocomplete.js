// Address autocomplete using OpenStreetMap Nominatim
let autocompleteTimeout;
const addressInput = document.getElementById('noteAddress');
const autocompleteContainer = document.createElement('div');
autocompleteContainer.className = 'address-autocomplete-dropdown';
autocompleteContainer.style.display = 'none';

if (addressInput) {
    addressInput.parentNode.style.position = 'relative';
    addressInput.parentNode.appendChild(autocompleteContainer);

    addressInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        
        if (query.length < 3) {
            autocompleteContainer.style.display = 'none';
            return;
        }

        clearTimeout(autocompleteTimeout);
        autocompleteTimeout = setTimeout(() => {
            searchAddress(query);
        }, 150);
    });

    document.addEventListener('click', function(e) {
        if (e.target !== addressInput && !autocompleteContainer.contains(e.target)) {
            autocompleteContainer.style.display = 'none';
        }
    });
}

async function searchAddress(query) {
    try {
        // Search Australia first (biased results)
        const auResponse = await fetch(
            `https://nominatim.openstreetmap.org/search?` +
            `q=${encodeURIComponent(query)}` +
            `&format=json` +
            `&addressdetails=1` +
            `&limit=8` +
            `&countrycodes=au` +
            `&accept-language=en`,
            {
                headers: {
                    'User-Agent': 'UrbanNotes/1.0'
                }
            }
        );
        const auResults = await auResponse.json();

        // Search worldwide (for international locations)
        const worldResponse = await fetch(
            `https://nominatim.openstreetmap.org/search?` +
            `q=${encodeURIComponent(query)}` +
            `&format=json` +
            `&addressdetails=1` +
            `&limit=5` +
            `&accept-language=en`,
            {
                headers: {
                    'User-Agent': 'UrbanNotes/1.0'
                }
            }
        );
        const worldResults = await worldResponse.json();

        // Combine and filter results
        const combined = [...auResults, ...worldResults];
        const filtered = filterResults(combined);
        displayResults(filtered);
    } catch (error) {
        console.error('Error fetching address suggestions:', error);
    }
}

function filterResults(results) {
    // Remove duplicates based on multiple criteria
    const seen = new Set();
    const unique = results.filter(result => {
        // Create a unique key from name + location
        const key = `${result.name}_${result.address?.city}_${result.address?.state}_${result.address?.country}`;
        
        if (seen.has(key)) {
            return false;
        }
        seen.add(key);
        return true;
    });

    // Filter out weird/irrelevant results
    const filtered = unique.filter(result => {
        const type = result.type;
        const osm_type = result.osm_type;
        
        // Exclude these types
        const excludeTypes = [
            'yes',
            'residential',
        ];
        
        // Excludes selected areas
        if (excludeTypes.includes(type)) {
            return false;
        }

        // Exclude if it's just an administrative relation
        if (osm_type === 'relation' && type === 'administrative') {
            return false;
        }

        return true;
    });

    // Prioritize Australia results, then other countries
    const australia = filtered.filter(r => r.address?.country === 'Australia');
    const other = filtered.filter(r => r.address?.country !== 'Australia');

    // Combine with Australia first, limit to 10 total
    return [...australia, ...other].slice(0, 10);
}
function displayResults(results) {
    if (results.length === 0) {
        autocompleteContainer.style.display = 'none';
        return;
    }

    autocompleteContainer.innerHTML = '';
    
    results.forEach(result => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        
        // Format the display - show name and compact location
        const name = result.name || result.address?.amenity || result.address?.tourism || 'Unknown';
        const location = formatCompactLocation(result.address);
        
        item.innerHTML = `
            <div class="autocomplete-main">${name}</div>
            <div class="autocomplete-detail">${location}</div>
        `;
        
        // Store full display name for when clicked
        item.addEventListener('click', function() {
            addressInput.value = result.display_name;
            autocompleteContainer.style.display = 'none';
        });
        
        autocompleteContainer.appendChild(item);
    });

    autocompleteContainer.style.display = 'block';
}

function formatCompactLocation(address) {
    if (!address) return '';
    
    const parts = [];
    
    // Build a compact location string
    if (address.suburb || address.neighbourhood) {
        parts.push(address.suburb || address.neighbourhood);
    } else if (address.city || address.town || address.village) {
        parts.push(address.city || address.town || address.village);
    }
    
    if (address.state) {
        parts.push(address.state);
    }
    
    if (address.postcode) {
        parts.push(address.postcode);
    }
    
    // Always add country name
    if (address.country) {
        parts.push(address.country);
    }
    
    return parts.join(', ');
}

// loading bar
addressInput.addEventListener('input', function(e) {
    const query = e.target.value.trim();
    
    if (query.length < 3) {
        autocompleteContainer.style.display = 'none';
        return;
    }

    clearTimeout(autocompleteTimeout);
    
    // Show loading immediately
    autocompleteContainer.innerHTML = '<div class="autocomplete-loading">🔍 Searching...</div>';
    autocompleteContainer.style.display = 'block';
    
    autocompleteTimeout = setTimeout(() => {
        searchAddress(query);
    }, 150);
});