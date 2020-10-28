#ZIPZAP server installer - an all in 1 button solution
#Created by Ju @ ZipZap 27/10/2020    
#Does not work on x32bit architectures
#Script Checks if people have python 3.8.0 and Visual studio redistribuatble before starting   

#Debug-Tracecalls


    # Main menu, allowing user selection
function Show-Menu
{
     param (
           [string]$Title = 'Easy Function Menu'
     )
     cls
     #Write-Host "`n`n                    ／人◕ ‿‿ ◕人＼                  `n`n"
     Write-Host "          WOULD YOU LIKE TO MAKE A CONTRACT?             `n" -BackgroundColor Magenta
     Write-Host "========= ZipZap: MagiReco NA Private Server  ===========`n" 
    
    Write-Host "1: Press '1' to install the MagiRecoServer and requirements."
    Write-Host "2: Press '2' to Run the Magireco Server."
    Write-Host "3: Press '3' to backup your account onto this server." #<-might not work after 30th of october
    Write-Host "Q: Press 'Q' to quit."
}


#Functions go here

Function GetCorrectIPv4Address {
#fork of get ip address
$i = (Get-NetIPConfiguration | Where-Object {
        $_.IPv4DefaultGateway -ne $null -and
        $_.NetAdapter.Status -ne "Disconnected"
    }
    ).IPv4Address.IPAddress

    return $i

}

Function InstallServer {


Write-Host "function 1 - Installation will now start"

Set-Location -Path $PSScriptRoot
$cwf = Get-Location

$test = "" + $cwf+"\env\Include"
$PIF = "" + $cwf+"\env\Include\python-3.8.0-amd64.exe"
$VCC = "" + $cwf+"\env\Include\VC_redist.x64.exe"
$requirementsFile = "" + $cwf+"\requirements.txt"
$VEN = "" + $cwf+"\env\Scripts\activate.bat"

Write-Host "Current working folder: " $cwf
Write-Host "Checking file integrity before requirement's installation"

if( !( ( test-path $PIF ) -and ( test-path $VCC ) -and (test-path $requirementsFile) -and (test-path $VEN) ))
{
    Write-Host "One of the files not found!"
    Write-Host "Make Sure you're running this script from the ZipZap folder!"
    break
}

Write-Host "Files Checked - Proceeding to install VC_Redist.x64 if not installed yet"
if(!(Test-path "HKLM:\SOFTWARE\Wow6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"))
{
    Write-Host "!!Visual Sutdio Runtime Library not found!!"
    Write-Host $VCC
    Write-Host "Installing now VC_Redist.x64... please wait..."
    Start-Process -FilePath “$VCC” -ArgumentList “/passive /log log.txt” -Wait
}

$VP = python --version
Write-Host "Checking current python version:" $VP

if($VP -ne "Python 3.8.0")
{

    Write-Host "!!Python not found or an older version is being used!!"-ForegroundColor red
    Write-Host $PIF
    Write-Host "Installing now python-3.8.0-amd64.exe ... please wait..."
    Write-Host "For real, wait. it's gonna take a little while."
    Start-Process -FilePath “$PIF” -ArgumentList “/quite InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1” -Wait
    cls
    Write-Host "Python finished, please open again this program so that the changes may be seen in the system ."
    break
}

cls
#fork of getstarted.bat
Write-Host "All pre-quisites installed.. proceeding to install python dependencies"

python -m venv ./env
Start-Process -FilePath “$VEN” -Wait
python -m pip install --upgrade pip
python -m pip install -r $requirementsFile


cls

Write-Host "All dependencies installed!"

$IPstuff = GetCorrectIPv4Address
Write-Host "THIS IS YOUR IP and PORT FOR YOUR PROXY: " -ForegroundColor Red 
Write-Host "Ip: $IPstuff `nPort: 8080 " -ForegroundColor Red -BackgroundColor Yellow
Write-Host "Now the preparations are done. You should configure the proxy on the Magia Record Device"

break
}

Function StartServer {

    Write-Host "Function 2 - Start MITM Server "-ForegroundColor green
   
    Set-Location -Path $PSScriptRoot
    $current = Get-Location

    $serverFile = "" + $current+"\server.py"
    $scriptFolder = "" + $current+"\env\Scripts"

    Write-Host "Current working folder: " $current
    Write-Host "Checking file integrity before initializing"

    if( !((test-path $serverFile) -and (test-path $scriptFolder)) )
    {
        Write-Host "One of the files not found! `nMake Sure you're running this script from the ZipZap folder!!"-ForegroundColor Red 
        break
    }

    #Checks passed -- select your server mode to run

     Write-Host "`n`n=============== Important Notice ===============`n`n"
    
     Write-Host "if you haven't backed up your account in your APK it will start with the AAAA default User."
     Write-Host "if you everything fails please copy the folder data\default_user to \data\user manually"
     Write-Host "If you want your account in the priv server please use the backup user function`n"
     Write-Host "NOTE: you may have to run the tutorial and download all the assets first if possible,we're working on a fix to have blank apks work."-ForegroundColor red



     Read-Host -Prompt "Press any key to continue..."

                    cls
                    
                    Write-Host "Starting MITM" -ForegroundColor green
                    Write-Host "`nClosing this console will turn off the proxyServer!`n" -ForegroundColor red
                    Write-Host "You can exit the server by pressing Ctrl+C in the console or closing this window."
                    Write-Host "NOTE: Closing your web-browser will not close the server and will continue running in the background!"

                    $IPstuff = GetCorrectIPv4Address
                Write-Host "THIS IS YOUR IP and PORT FOR YOUR PROXY: " -ForegroundColor Red 
                   Write-Host "Ip: $IPstuff `nPort: 8080 " -ForegroundColor Red -BackgroundColor Yellow

                    $r = "mitmweb.exe -s server.py"
                    iex $r
      

   
    break
}

Function BackUpUser{

    Write-Host "Function 3 - Back up data "-ForegroundColor green
   
    Set-Location -Path $PSScriptRoot
    $current = Get-Location

    $serverFile = "" + $current+"\transferUserData.py"
    $userFile = "" + $current+ "\getUserData.py"
    $scriptFolder = "" + $current+"\env\Scripts"

    Write-Host "Current working folder: " $current
    Write-Host "Checking file integrity before initializing"

    if( !((test-path $serverFile) -and (test-path $userFile) -and (test-path $scriptFolder) ) )
    {
        Write-Host "One of the files not found! `nMake Sure you're running this script from the ZipZap folder!!"-ForegroundColor Red 
        break
    }

    Write-Host "========= File backup  ===========`n" 
    Write-Host "1: Press '1' to transfer your data from the NA magireco server. (might not work after 30th of oct/2020)"
    Write-Host "2: Press '2' to transfer data from your device with the account already in it. (might not save all your info)"


     $input3 = Read-Host "Please make a selection"
     switch ($input3)
     {
         '1' {
                    Start-Process "transferUserData\transferUserData.exe" -Wait
                  
           } '2' {
            Write-Host "Please connect now your magireco app with your data in it to this server"
            
            $IPstuff = GetCorrectIPv4Address
            Write-Host "THIS IS YOUR IP and PORT FOR YOUR PROXY: " -ForegroundColor Red 
            Write-Host "Ip: $IPstuff `nPort: 8080 " -ForegroundColor Red -BackgroundColor Yellow

            $rb = "mitmweb.exe -s getUserData.py"
            iex $rb
           
           }
     
     }


}





#Main menu loop
do
{

#check if running as admin
    If (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(`

    [Security.Principal.WindowsBuiltInRole] “Administrator”))

{

    Write-Warning “You do not have Administrator rights to run this script!`nPlease re-run this script as an Administrator!”

    Break

}
#proceed to main menu
     Clear-Host
     Show-Menu
     
     $input = Read-Host "Please make a selection"
     switch ($input)
     {
           '1' {
                cls
                InstallServer
           } '2' {
                 
                cls
                StartServer
           } '3' {
                
                cls
                BackUpUser

                
           } 'q' {
                return
           }
     }
     pause
}
until ($input -eq 'q')