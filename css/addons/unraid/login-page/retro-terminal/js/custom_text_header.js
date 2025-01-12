
 //Custom Text Header //
 // ACSII slant font

// Needs to be inside <section id="login" class="shadow">
// YOU MUST ESCAPE ANY SINGLE BACKSLASHES LIKE SO: \\

let custom_text_header = `
<div class="custom-text-header"> <pre>

  /$$$$$$  /$$                                       /$$    
 /$$__  $$| $$                                      | $$    
| $$  \__/| $$   /$$ /$$   /$$ /$$$$$$$   /$$$$$$  /$$$$$$  
|  $$$$$$ | $$  /$$/| $$  | $$| $$__  $$ /$$__  $$|_  $$_/  
 \____  $$| $$$$$$/ | $$  | $$| $$  \ $$| $$$$$$$$  | $$    
 /$$  \ $$| $$_  $$ | $$  | $$| $$  | $$| $$_____/  | $$ /$$
|  $$$$$$/| $$ \  $$|  $$$$$$$| $$  | $$|  $$$$$$$  |  $$$$/
 \______/ |__/  \__/ \____  $$|__/  |__/ \_______/   \___/  
                     /$$  | $$                              
                    |  $$$$$$/                              
                     \______/                               

</pre> </div>
`;
document.getElementById("login").innerHTML += custom_text_header
