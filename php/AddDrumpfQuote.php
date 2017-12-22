<?php

/*

REQUIREMENTS

* A custom slash command on a Slack team
* A web server running PHP5 with cURL enabled

USAGE

* Place this script on a server running PHP5 with cURL.
* Set up a new custom slash command on your Slack team: 
  http://my.slack.com/services/new/slash-commands
* Under "Choose a command", enter whatever you want for 
  the command. /isitup is easy to remember.
* Under "URL", enter the URL for the script on your server.
* Leave "Method" set to "Post".
* Decide whether you want this command to show in the 
  autocomplete list for slash commands.
* If you do, enter a short description and usage hint.

*/

# Grab some of the values from the slash command, create vars for post back to Slack
$command = $_POST['command'];
$text = $_POST['text'];
$token = $_POST['token'];
$user_name = $_POST['user_name'];

# Grab configuration information from configuration file
$config_array = parse_ini_file("AddDrumpfQuote.ini");
#echo $config_array['quoteFile'];

# Check the token and make sure the request is from our team 
#echo strpos($config_array['slashTokens'],$token);
#if($token != 'hNEHjC9g0dHEfeRY4fVOS8u3' AND $token != 'VX7miQU1LBnHjzA2uZBweLhJ'){ #replace this with the token from your slash command configuration page
if(strpos($config_array['slashTokens'],$token) == false AND strpos($config_array['slashTokens'],$token) !== 0){
  echo "The token for the slash command doesn't match. Check your script.";
  die($msg);
}

## Write new quote to TrumpQuotes file
# Identify file to add quote to
$filename = $config_array['quoteFile'];

# Open file and add quote
if (is_writable($filename)) {
    if (!$handle = fopen($filename, 'a')) {
         echo "Cannot open file ($filename)";
         exit;
    }

    // Write $text to our opened file.
    if (fwrite($handle, "\n".$text) === FALSE) {
        echo "Cannot write to file ($filename)";
        exit;
    }

    echo $config_array['responseMessage'];

    fclose($handle);

} else {
    echo "The file $filename is not writable";
}

## Log new quote
# Identify file to add quote to
$filename = $config_array['logFile'];

# Open file and add quote
if (is_writable($filename)) {
    if (!$handle = fopen($filename, 'a')) {
         echo "Cannot open file ($filename)";
         exit;
    }

    // Write $text to our opened file.
    if (fwrite($handle, "\n".date("Y.m.d.h.i.sa")." - ".$user_name." added: ".$text) === FALSE) {
        echo "Cannot write to file ($filename)";
        exit;
    }

    fclose($handle);

} else {
    echo "The file $filename is not writable";
}