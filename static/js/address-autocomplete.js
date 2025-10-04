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

        // Debounce the API calls
        clearTimeout(autocompleteTimeout);
        autocompleteTimeout = setTimeout(() => {
            searchAddress(query);
        }, 300);
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target !== addressInput && !autocompleteContainer.contains(e.target)) {
            autocompleteContainer.style.display = 'none';
        }
    });
}

async function searchAddress(query) {
    try {
        // Nominatim API - bias towards Australia
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?` +
            `q=${encodeURIComponent(query)}` +
            `&format=json` +
            `&addressdetails=1` +
            `&limit=5` +
            `&countrycodes=au` + // Bias to Australia
            `&accept-language=en`,
            {
                headers: {
                    'User-Agent': 'UrbanNotes/1.0' // Required by Nominatim
                }
            }
        );

        const results = await response.json();
        displayResults(results);
    } catch (error) {
        console.error('Error fetching address suggestions:', error);
    }
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
        
        // Format the display name nicely
        const displayName = result.display_name;
        
        item.innerHTML = `
            <div class="autocomplete-main">${result.name || result.display_name.split(',')[0]}</div>
            <div class="autocomplete-detail">${displayName}</div>
        `;
        
        item.addEventListener('click', function() {
            addressInput.value = displayName;
            autocompleteContainer.style.display = 'none';
        });
        
        autocompleteContainer.appendChild(item);
    });

    autocompleteContainer.style.display = 'block';
}