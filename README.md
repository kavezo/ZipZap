# ZipZap: MagiReco NA Private Server

You need to have a computer to run the server on, and a device with MagiReco to connect to it (both emulator and real 
physical device work).

To update to a new release: download the release, unzip it without overwriting the old one, then copy your data/user
folder from the old one to the new one

### On the computer: installation and running

On Windows, if you have Python 3.8 installed (with pip, and with python added to PATH -- look out for these options when
installing), you can just run getStarted.bat and then startServer.bat. You can close the browser window that pops up but 
not the command line.

If you don't have Windows,
1. Make sure you have python3, either in a separate env (recommended because system-wide Python dependency graphs are 
gross) or on your system
2. Run `pip install -r requirements.txt` in a command line
3. Run `mitmproxy -s server.py` or `mitmweb -s server.py` in a command line, and do not close this command line. (If you
run mitmweb though, you can close the browser window.)

### On your phone/tablet/emulator: connecting to the private server

1. Make sure MagiReco is already installed on your device. I've only tested it on when it's past the tutorial, so no 
guarantees it'll work for a fresh install. But it works even if you haven't updated.
2. Find the IP address of the computer you're running the server on. I've only tested this with a local IP address (ones
that start with 192.168) but external IP addresses should work.
3. Configure a proxy on your device with the server address as your computer's IP address, and the port as 8080. You can
google this if you don't know how to.
4. By the way, if you're new to this, this needs to be done with the server running on your computer.
5. Open mitm.it in a browser, and download and enable a certificate for your device
6. Try loading google.com through the proxy -- if it works, then you can open the app and everything will be through the
private server.

I had a horrible time getting mitmproxy to work on some of my devices; specifically, I never got it to work with my Mac
running mitmproxy and my iPhone 6 trying to get through it. Try googling any errors you have with mitmproxy; it may or
may not help. In the future I might move off of mitmproxy and find a different solution.

If you have trouble, check the original Reddit post -- the comments have a lot of common problems and ways people resolved
them. Also, the official Magia Record discord has some amazing volunteers helping debug in the #en-closure channel right 
now.

---
### Porting over your existing data

#### The easy way
Start the server and connect your phone to it. Use the transfer button, and put your info in. This will erase your data 
on the real server, though, so you'll have to transfer it back if you still want to play it on your device.

#### The standalone way
If you have trouble getting the server running and you're on Windows, delete the data/user folder and run 
transferUserData.bat. If you're not on Windows and have Python, you can run `pip install -r requirements.txt` and then 
`python transferUserData.py`.

---
### Configuration

By default, the app makes all requests to the cloud. If your internet is slow, this will also make the app significantly
laggier than it usually is, and you might want to store the assets to serve from disk. All the assets will take up about 3GB
of space, but they'll only be pulled from the cloud as needed. To do this, change the value of diskAssets in config.json to
true.

If you want to have all the assets on disk instead of downloading them as needed, you can pull everything from 
https://github.com/kavezo/MagiRecoStatic into the assets folder.

---

### Currently supported functions:
- displaying any page in the app (api/page.py)
    + as well as displaying anything in the archive
    + and listing memoria
- improving magical girls (api/userCard.py)
    - level up
    - magia level up
    - awaken
    - limit break
    - customize magical girls' looks (in disks, etc.)
- making teams with magical girls and memoria (api/userDeck.py)
- managing memoria (api/userPiece.py and api/userPieceSet.py)
    - level up
    - limit break
    - making memoria sets
    - putting memoria into the vault and taking them out
- gacha (api/gacha.py)
    - pull premium, x1 and x10, using stones and tickets
        - this currently includes all limited megucas and memes, and welfare ones as well. no reason not to lol
    - pull normal
    - view history
- changing user settings (api/gameUser.py, api/user.py, api/userChara.py)
    - set name
    - set comment
    - set leader
    - set background (only two backgrounds are available, but...)
- buying things from the shop (api/shop.py)
    - spending items to get items
    - spending gems to get packs
    - you can get megucas too, but they won't show up in your present box and instead you'll just have them

### Currently missing functions:
- can't recover AP
- can't lock or sell memoria
- you can't clear any missions or accept their rewards
- mirrors and quests are entirely nonfunctional

### What's next?
I coded very fast, and very not well, because I wanted to get as many features out before the 30th. Code quality is still
important to me, though, and I really don't want to get anything done outside of the basics before improving it enough
that maintenance will not be horrendous. But before the 30th, my priority is to get all the basic functions implemented
so that we won't have to rely on hitting the real server to figure out what it does for some important thing like 
battles.

The features are in order of the most overlap with the knowledge I have currently, to the least, because when I 
implement a new feature I don't know much about at least half of the time is spent researching how it fits in with all 
the user's data.

- implement quests
- implement mirrors
- implement missions
- implement tutorial 
- implement random things I left off, like AP recovering, login bonuses, and announcements
- add unit tests
- refactor
    - put all the data reading and writing into a util module to avoid race conditions with 50 different functions 
    writing/reading to a file at the same time
    - improve response headers, perhaps add compression
    - maybe make a class each API has to extend that removes repeated code?
    - maybe make classes that represent each type of object used in the game (e.g. item, card, userCard)?
- add support for events
- add support for multiple users (using a database like S3)
- add support for finding other users, following and using supports
- move server to the cloud
- hack app to call the server's address rather than having to rely on mitmproxy

### Structure of this package
As you can tell from the instructions, server.py is the main event handler. It intercepts requests from the app thanks
to mitmproxy, and decides what to do.

Most resources are going to be retrieved from an archive. For now that's en.rika.ren, but I don't know anything about
rika.ren other than that it stores assets, and I might switch to my own archive later if we want to have custom assets 
(like if we want to bring JP events in).

The exception is website assets (html, js, css, and the like). These are stored locally because they're small in size,
not likely to change, storing them speeds up loading, and we might want to edit them later to support new features like
setting a bunch of awaken mats at once, or SE. These are stored in the assets folder.

User data right now is stored locally as well, in the data/user directory. You can actually modify the files in here to
change which megucas or memes or items you have. Just be careful or the app will error if you messed up on a line or 
something.

All the support for different API endpoints is stored in the api directory; each endpoint has its own file. They all
take a request from the app, and generate the response. They edit the user data files directly, and also access the
general data files in the data directory that store things like a list of all the megucas in the game.

The page endpoint handles all of the info that the app needs to display different views, like the "Magical Girls"
screen or the different shops. None of the other endpoints are called until you actually try to change the user's
game data.

----
If you have suggestions or want to help, please contact me at
u/rhyme_or_rationale or rins_fourier_transform#2303. And feel free to send a pull request 
anytime~
