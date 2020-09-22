CREATE TABLE players (discord_id int unique, points int)
CREATE TABLE owned_items (discord_id INT UNIQUE, item_type INT, scrip TEXT, FOREIGN KEY(item_type) REFERENCES items(item_type))
CREATE TABLE items (item_type INT, description TEXT, price INT)
