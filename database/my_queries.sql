SELECT * FROM notes WHERE note_ID LIKE '3';

SELECT * FROM userinformation2 WHERE user_created LIKE '2025-08-22 13:30:48';

SELECT * FROM userinformation2 db WHERE LENGTH(user_name) = 7;

SELECT * FROM notes WHERE ( user_ID % 2 ) = 0 AND address LIKE "%UK%";

SELECT * FROM notes JOIN userinformation2 ON notes.user_id = userinformation2.user_id WHERE ( user_name % 2 ) = 0 AND note_title LIKE "%Transit%";