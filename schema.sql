CREATE TABLE players (discord_id INT unique, points INT)
CREATE TABLE owned_items (discord_id INT UNIQUE, item_type INT, scrip TEXT, FOREIGN KEY(item_type) REFERENCES items(item_type))
CREATE TABLE items (item_type TEXT, description TEXT, price INT, image_name TEXT)
