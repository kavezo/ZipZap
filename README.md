# ZipZap: MagiReco NA Private Server

You need to have a computer to run the server on, and a device with MagiReco to connect to it (both emulator and real 
physical device work).

To update to a new release: download the release, unzip it without overwriting the old one, then copy your data/user
folder from the old one to the new one.

### On the computer: installation and running

The first time before you run the server on Windows, you need to do some setup:
1. Run setupServer.bat.
2. Three cmd windows should pop up. One of them may immediately say "ERROR: The process "nginx.exe" not found."; you can close
this safely. Wait until the others close by themselves.
3. There should now be a new file named "ca.crt" in the server directory. Install this certificate on your phone.

You only need to do this once.

Then, to actually run the server, run startServer.bat. Two cmd windows should pop up without immediately closing; don't 
close either of them until you want to stop the server. That's all.

Currently, there isn't support for other systems out of the box. You'll have to get nginx for your system, copy over the
conf in windows/nginx, and run `makecert.sh` in the directory where certs are stored for nginx. Then, if you have Python 3,
you can run `pip install -r requirements.txt`. Finally, to start the server, in two separate terminals, you'll need to run 
nginx, and `python gevent_server.py`.

The server runs on a flask backend and nginx frontend, and uses a custom DNS server to redirect all requests to
android.magica-us.com and ios.magica-us.com to the computer running it. Currently there's no way to config the ports that
the server uses, but it needs 8022 for DNS, 5000 for flask, and 443 for nginx.

### On your phone/tablet/emulator: connecting to the private server

0. Run the server on your computer, and keep it running.
1. Make sure MagiReco is already installed on your device. I've only tested it on when it's past the tutorial, so no 
guarantees it'll work for a fresh install. But it works even if you haven't updated.
2. Find the IP address of the computer you're running the server on. I've only tested this with a local IP address (ones
that start with 192.168) but external IP addresses should work.
3. Open https://raw.githubusercontent.com/kavezo/ZipZap/https/windows/nginx_windows/nginx/conf/cert/ca.crt in a browser, 
and download and install the certificate for your device.
4. Change your DNS settings to point to your IP address.

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

----
If you have suggestions or want to help, please contact me at
u/rhyme_or_rationale or rins_fourier_transform#2303. And feel free to send a pull request 
anytime~
