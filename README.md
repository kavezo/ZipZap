# ZipZap: MagiReco NA Private Server

**Please be mindful when sharing.** We don’t want Aniplex shutting down NA yet again, so please keep this off of
mainstream social media sites. In fact, when you do share, please add a reminder to keep it off social media.

You need to have a computer to run the server on, and a device with MagiReco to connect to it (both emulator and real 
physical device work).

To update to a new release: download the release, unzip it without overwriting the old one, then copy your data/user
folder from the old one to the new one. If you don't want to install a new cert to your phone every time you update, also 
copy the (windows/nginx_windows/)nginx/conf/cert from the old to the new.

### On the computer: installation and running

For Windows, please download a release rather than the source code.

The first time before you run the server on Windows, you need to do some setup:
1. Run setupServer.bat.
2. A cmd window should pop up. Wait until it closes by itself.
3. There should now be a new file named "ca.crt" in the server directory. Install this certificate on your phone -- on 
Android you can just move it on there and install it through settings/security, but on iOS you have to email it to 
yourself or download it through Safari, then make sure you trust it through Certificate Trust Settings after it's 
installed.

You only need to do this once. (Although if you ever run setupServer.bat again, you'll have to repeat step 3.)

Then, to actually run the server, run startServer.bat. A cmd window should pop up without immediately closing; don't 
close it until you want to stop the server. That's all.

#### Alternate installation method

An alternate method is available that will run ZipZap in its own self-contained Linux virtual machine. This method can be 
used on Windows, Mac and Linux. For this, you will need to download the source code rather than the release.

You will need to download and install [VirtualBox](https://www.virtualbox.org/) (**be sure and also download and install
the VirtualBox Guest Additions**) as well as [Vagrant](https://www.vagrantup.com/). Both of these apps are completely
free for personal/non-commercial use. Once these are installed, simply open a terminal in the server window and type 
`vagrant up`. This will automatically configure ZipZap and run it.

In some rare cases, Vagrant will ask you for which network interface you would like to use as the bridge interface.
Usually the topmost choice is the right one, but in some rare instances you will have to choose one of the other
options. If the option you choose didn't work, run `vagrant destroy` followed by `vagrant up` and try a different
choice.

Once the configuration process is complete, the script will display the VM's IP address. On your device or emulator,
set the DNS server to that IP address, then open a web browser and go to `https://magica-us.com`. You should see a page
asking you to install the custom SSL certificate. Follow the instructions to do this. Now you should be able to run
Magia Record and connect to your private server!

To start up the private server VM, run `vagrant up`; and to shut it down run `vagrant halt`.

### On your phone/tablet/emulator: connecting to the private server

0. Run the server on your computer, and keep it running.
1. Make sure MagiReco is already installed on your device. I've only tested it on when it's past the tutorial, so no 
guarantees it'll work for a fresh install. But it works even if you haven't updated.
2. Find the IP address of the computer you're running the server on. I've only tested this with a local IP address (ones
that start with 192.168) but external IP addresses should work.
3. Change your DNS settings to point to your IP address. On iOS you can do this by editing the network settings as you
would with a proxy (just make sure to edit DNS, not proxy, settings), but on Android emulator I've had to use a 
different app. The one I use is just called DNS Changer, and its icon is a blue circle with DNS in it.

### A note about Android 7 (Nougat) and above

Due to a change that Google made starting in Android 7 (Nougat)
[user-installed CA certificates are no longer trusted by apps](https://android-developers.googleblog.com/2016/07/changes-to-trusted-certificate.html).
In order to play on devices and/or emulators running Android 7 and above, you will need to be rooted, and will need to
install the ZipZap CA certificate as a System (trusted) certificate. [This Magisk plugin](https://github.com/NVISO-BE/MagiskTrustUserCerts)
will automatically take care of this for you.

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
