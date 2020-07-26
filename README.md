# Samurai Shodown V Special - Move Data Scraper

I wrote this Python utility to assist in a side project. It uses the Mizuumi wiki page for Samurai Shodown V Special to gather the move data for each character in the game, formats the data in a more sql(ite) frinedly manner, and finally pushes the parsed information to a local sqlite database that has already been created.

There are a bit over 1000 moves since each character has normal ground attacks, normal air attacks, normal ground attacks that can only be used if said character is on top of an opponent (referred to as a "near" move by the community), so going through it by hand would have been a monumental task (props to the fighting games fans maintaining Mizuumi).

For this project, there are certain things I'm not afraid of such as SQL injection due to the nature of the data I'm gathering. This project also makes certain assumptions that fit my needs. For example:

- I already have the database file ready
- I'm sending everything to a particular existing table, not generating the tables in the database
- I already have a table for the characters in the game
- There are certain decisions I'm willing to make in terms of returning null, i.e., some values for frame data are just 'Y' as in "yes, this move can have its wind-down animation cancelled into another normal or a special move" and I return `None` for those

The utility could be more performant and less leaky in terms of abstractions since I gather all of the data into data transfer objects and then eschew the idea of a DTO by writing a `toTuple` method for the class; having them as tuples allows me to leverage `sqlite3`'s `executemany` method. I already did the work and I have the data already stored in the table, but I think for future projects/scrapers like this, I might have to ask on the internet for some help. I have another scraper in the works for a similar task with a bunch of work already done, but I think now I can at least press the pause button on that project and attempt to right any design/structure wrongs while I still can.
