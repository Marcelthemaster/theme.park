
 //Custom Text Header //
 // ACSII slant font

// Needs to be inside <section id="login" class="shadow">
// YOU MUST ESCAPE ANY SINGLE BACKSLASHES LIKE SO: \\

let custom_text_header = `
<div class="custom-text-header"> <pre>
  _____     _             _   _____                   _                      _             
 | ____|___| | _____ _ __| |_| ____|_ __   __ _ _ __ (_)_ __   ___  ___ _ __(_)_ __   __ _ 
 |  _| / __| |/ / _ \ '__| __|  _| | '_ \ / _` | '_ \| | '_ \ / _ \/ _ \ '__| | '_ \ / _` |
 | |__| (__|   <  __/ |  | |_| |___| | | | (_| | | | | | | | |  __/  __/ |  | | | | | (_| |
 |_____\___|_|\_\___|_|   \__|_____|_| |_|\__, |_| |_|_|_| |_|\___|\___|_|  |_|_| |_|\__, |
                                          |___/                                      |___/ 
</pre> </div>
`;
document.getElementById("login").innerHTML += custom_text_header
