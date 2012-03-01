# TeamSpeak Notifier

Using TeamSpeak as your office communication channel can be difficult-- especially
if you don't have your headphones on.

This application will watch for incoming messages in Teamspeak and, should you
be in a different window, display a notification to let you know that you
recieved a message.

## Requirements

 - PyGTK
 - teamspeak3

## Use

You can either run the program directly like:

    teamspeak-notifier &

Add it to your automatically started applications.

## Arguments

You can run it with any of the following arguments:

 - **--info** Allows you to see information about communication with Teamspeak.
 - **--debug** Allows you to see more information than the above.
 - **--logfile**  Allows you to specify a file to log errors to.


