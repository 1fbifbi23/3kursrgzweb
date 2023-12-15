-- CREATE USER admin_rgz_larionov_base WITH PASSWORD '123';
-- CREATE DATABASE rgz_larionov_base WITH OWNER admin_rgz_larionov_base;

CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(500) NOT NULL
);

-- Создание таблицы "Анкеты"
CREATE TABLE Profiles (
    id SERIAL PRIMARY KEY,
    user_id INT,
    age INT,
	name VARCHAR(50) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    searching_for VARCHAR(10) NOT NULL,
    about_me TEXT,
    photo VARCHAR(500),
    hide_profile BOOLEAN,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
select * from users;
select * from Profiles;
--Drop table users;
--drop table profiles;


GRANT ALL ON TABLE public.users TO admin_rgz_larionov_base;;
GRANT ALL ON TABLE public.Profiles TO admin_rgz_larionov_base;;
GRANT usage ON SEQUENCE users_user_id_seq TO admin_rgz_larionov_base;;
GRANT usage ON SEQUENCE profiles_id_seq TO admin_rgz_larionov_base;;











