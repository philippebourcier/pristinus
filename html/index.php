<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pristinus Configuration</title>
  <link rel="stylesheet" href="css/jquery-ui.css">
  <script src="js/jquery-1.12.4.js"></script>
  <script src="js/jquery-ui.js"></script>
<script>
  $( function() {

    $("input:checkbox").checkboxradio();
    $(".toggles").controlgroup( { direction: "vertical" } );

    $( "#slider" ).slider({
      range: "max",
      min: 10,
      max: 300,
<?php

$r="";
if($_POST["r_23"]=="on") $r.="23\n";
if($_POST["r_24"]=="on") $r.="24\n";
file_put_contents("/opt/pristinus/data/pristinus_relays.txt",$r);

if($_POST["lsec"]!=null) file_put_contents("/opt/pristinus/data/pristinus_sleep.txt",$_POST["lsec"]."\n");

sleep(0.25);

$zsleep=@file_get_contents("/opt/pristinus/data/pristinus_sleep.txt");
if($zsleep===FALSE) echo("value: 30,");
else echo("value: ".trim($zsleep).",");

?>
      slide: function(event,ui) {
	      if($("#save").attr("disabled")) $("#save").attr("disabled",false);
	      $("#amount").val(ui.value);
      }
    });

    $("#amount").val($("#slider").slider("value"));

<?php

if($_POST["lsec"]!=null) echo("$(\"#save\").attr(\"disabled\",true);\n");

$relays=explode("\n",@file_get_contents("/opt/pristinus/data/pristinus_relays.txt"));
for($i=0,$max=count($relays);$i<$max;$i++) if($relays[$i]!="") echo '$("#r_'.$relays[$i].'").attr("checked",true);'."\n";

?>

    $("input:checkbox").checkboxradio( "refresh" );
    $("input:checkbox").bind('change', function() {
             if($("#save").attr("disabled")) $("#save").attr("disabled",false);
    });

  } );
  </script>
  <style>
    .border { border: 2px solid #333333; }
    .toggles { width: 400px; }
body {
	font-family: Arial, Helvetica, sans-serif;
}

table {
	font-size: 1em;
}

.ui-draggable, .ui-droppable {
	background-position: top;
}
  </style>
</head>
<body>

<br/><br/><br/>
<blockquote>
<form method="POST" action="/">
<p>
  <label for="amount">Number of seconds to run UVC LEDs :</label>
  <input name="lsec" type="text" id="amount" readonly style="border:0; color:#f6931f; font-weight:bold;">
</p>
<div id="slider"></div>
<br/><br/>
<div class="widget">
<fieldset>
   <br/>
	<legend>LED Selection : </legend>

<blockquote>
    <br/>
    <div class="toggles">
      <label for="r_24">Top 36 LEDs 0.2W 265nm 14mJ</label>
      <input class="toggle" type="checkbox" name="r_24" id="r_24">
      <br/><br/>
      <label for="r_23">Sides 2x36 LEDs 0.5W 277nm 10mJ</label>
      <input class="toggle" type="checkbox" name="r_23" id="r_23">
    </div>
   <br/><br/>
</blockquote>

</fieldset>
</div>
<br/><br/>
<input id="save" style="float: right;" class="ui-button ui-widget ui-corner-all" type="submit" value="SAVE">
</form>
</blockquote>
 
</body>
</html>
