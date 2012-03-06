<?php
$url = $_GET["url"];
$html = file_get_contents($url);
$data = json_encode(array('html'=>$html));


if(isset($_GET['callback']))				
				echo $_GET['callback']."(" . $data. ")";
else
echo $data;
?>