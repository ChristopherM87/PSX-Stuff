# Need to set trustedhosts on the server that will run this script: set-item -path wsman:\localhost\client\trustedhosts -value "192.168.198.1,192.168.198.2,192.168.198.3"
# Then create cred.txt file: read-host -assecurestring | convertfrom-securestring | out-file C:\PSX\cred.txt

$password = Get-Content ‘C:\psx\cred.txt’ | ConvertTo-SecureString

#Login to for pc1
$credentials = new-object -typename System.Management.Automation.PSCredential -argumentlist "pc1\psx",$password

#Copy Aerowinx.jar to pc1
$Session = New-PSSession -ComputerName 192.168.198.1 -Credential $credentials
Copy-Item -Path C:\PSX\updates\Aerowinx.jar -Destination C:\PSX\Aerowinx\Aerowinx.jar -ToSession $session

#Login to for pc2
$credentials = new-object -typename System.Management.Automation.PSCredential -argumentlist "pc2\psx",$password

#Copy Aerowinx.jar to pc2
$Session = New-PSSession -ComputerName 192.168.198.2 -Credential $credentials
Copy-Item -Path C:\PSX\updates\Aerowinx.jar -Destination C:\PSX\Aerowinx\Aerowinx.jar -ToSession $session

#Login to for pc3
$credentials = new-object -typename System.Management.Automation.PSCredential -argumentlist "pc3\psx",$password

#Copy Aerowinx.jar to pc3
$Session = New-PSSession -ComputerName 192.168.198.3 -Credential $credentials
Copy-Item -Path C:\PSX\updates\Aerowinx.jar -Destination C:\PSX\Aerowinx\Aerowinx.jar -ToSession $session
