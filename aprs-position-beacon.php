<?php
/*  Requirments include gpsd with a local websever serving up
    https://raw.githubusercontent.com/yazug/gpsd/master/gpsd.php.in.

    In addition, the following AFSK/APRS python library is required:
    https://github.com/casebeer/afsk (pip install afsk)
    PyAudio not required.

lat = 34.4928563
lon = -117.4086769
*/

function process_gps() {

	// Settings & variables
	$callsign = "N0CALL-11";			// Your callsign
	$comment = "WP10 ";		// APRS comment

	//$url = 'http://localhost/gpsd.php?op=json';
	//$content = file_get_contents($url);
	//$json = json_decode($content, true);

	// Time 2015-11-03T02:04:14.000Z
	//$time = $json['tpv'][0]['time'];
	$time = "2018-02-07T21:47:14.000Z";
	echo "Time: ".$time;
	$timeday = substr($time, 8, 2);
	$timehour = substr($time, 11, 2);
	$timeminute = substr($time, 14, 2);
	$time = $timeday.$timehour.$timeminute; //092345 day:hour:minute UTC/Z

	// Latitude 34.4928563
	//$lat = $json['tpv'][0]['lat'];
	$lat = "34.4928563";
	$latday = substr($lat, 0, 2);
	$latmin = round(substr($lat, 2) * 60, 2);
	$latmin = number_format($latmin, 2, '.', '');
	if (strlen($latmin) == 4) {
		$latmin = "0".$latmin;
	}
	$lat = $latday.$latmin; // 3548.38

	// Longitude -117.408676
	//$lon = explode(".", $json['tpv'][0]['lon']);
	$lon[0] = "-117.408676";
	$londay = substr($lon[0], 1);
	if (strlen($londay) == 2) {
	    $londay = "0".$londay;
	} else if (strlen($londay) == 1) {
	    $londay = "00".$londay;
	}
	$lonmin = ".".$lon[1];
	$lonmin = round($lonmin * 60, 2);
	$lonmin = number_format($lonmin, 2, '.', '');
	if (strlen($lonmin) == 4) {
	    $lonmin = "0".$lonmin;
	}
	$lon = $londay.$lonmin; // 08621.53

	//$course = round($json['tpv'][0]['track']);
	$course = "90";
	if (strlen($course) == 1) {
		$course = "00".$course;
	} else if (strlen($course) == 2) {
		$course = "0".$course;
	}

	//$speed = $json['tpv'][0]['speed'] * 1.9438444924574;
	$speed = "1";
	$speed = round($speed);
	if (strlen($speed) == 1) {
		$speed = "00".$speed;
	} else if (strlen($speed) == 2) {
		$speed = "0".$speed;
	}

	// Altitude 192.910 meters
	//$alt = round($json['tpv'][0]['alt'] * 3.2808); // Convert meters to feet
	$alt = "3285";

	if ( strlen($alt) == 1 ) {
		$alt = "00000".$alt;
	} else if ( strlen($alt) == 2 ) {
		$alt = "0000".$alt;
	} else if ( strlen($alt) == 3 ) {
		$alt = "000".$alt;
	} else if ( strlen($alt) == 4 ) {
		$alt = "00".$alt;
	} else if ( strlen($alt) == 5 ) {
		$alt = "0".$alt;
	} // 000633 feet

	$command = 'aprs -c '.$callsign.' -o packet.wav "/'.$time.'z'.$lat.'N/'.$lon.'W>'.$course.'/'.$speed.$comment.'/A='.$alt.'"';

	echo "\n";
	echo "Time: ".$time;
	echo "\n";
	echo "Latitude: ".$lat;
	echo "\n";
	echo "Longitude: ".$lon;
	echo "\n";
	echo "Altitude: ".$alt;
	echo "\n";
	echo "Track: ".$course;
	echo "\n";
	echo "Speed: ".$speed;

	echo "\n\n";
	echo $command;

	if ($lat == 0) {
		echo "\n\nNo GPS data is available.\n";
	} else {
		echo "\n\nBuilding beacon audio...\n";
		exec($command);
		sleep(2);
		echo "\n\nTransmitting beacon\n";
		exec("aplay packet.wav");
	}

	//sleep(15);
	//process_gps();

}

echo "\n";
process_gps();
echo "\n";

?>
