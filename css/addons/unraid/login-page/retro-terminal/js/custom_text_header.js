
 //Custom Text Header //
 // ACSII slant font

// Needs to be inside <section id="login" class="shadow">
// YOU MUST ESCAPE ANY SINGLE BACKSLASHES LIKE SO: \\

let custom_text_header = `
<div class="custom-text-header"> <pre>

$$$$$$$$\          $$\                            $$\     $$$$$$$$\                               $$\                                         $$\                     
$$  _____|         $$ |                           $$ |    $$  _____|                              \__|                                        \__|                    
$$ |      $$$$$$$\ $$ |  $$\  $$$$$$\   $$$$$$\ $$$$$$\   $$ |      $$$$$$$\   $$$$$$\  $$$$$$$\  $$\ $$$$$$$\   $$$$$$\   $$$$$$\   $$$$$$\  $$\ $$$$$$$\   $$$$$$\  
$$$$$\   $$  _____|$$ | $$  |$$  __$$\ $$  __$$\\_$$  _|  $$$$$\    $$  __$$\ $$  __$$\ $$  __$$\ $$ |$$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$ |$$  __$$\ $$  __$$\ 
$$  __|  $$ /      $$$$$$  / $$$$$$$$ |$$ |  \__| $$ |    $$  __|   $$ |  $$ |$$ /  $$ |$$ |  $$ |$$ |$$ |  $$ |$$$$$$$$ |$$$$$$$$ |$$ |  \__|$$ |$$ |  $$ |$$ /  $$ |
$$ |     $$ |      $$  _$$<  $$   ____|$$ |       $$ |$$\ $$ |      $$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |$$ |  $$ |$$   ____|$$   ____|$$ |      $$ |$$ |  $$ |$$ |  $$ |
$$$$$$$$\\$$$$$$$\ $$ | \$$\ \$$$$$$$\ $$ |       \$$$$  |$$$$$$$$\ $$ |  $$ |\$$$$$$$ |$$ |  $$ |$$ |$$ |  $$ |\$$$$$$$\ \$$$$$$$\ $$ |      $$ |$$ |  $$ |\$$$$$$$ |
\________|\_______|\__|  \__| \_______|\__|        \____/ \________|\__|  \__| \____$$ |\__|  \__|\__|\__|  \__| \_______| \_______|\__|      \__|\__|  \__| \____$$ |
                                                                              $$\   $$ |                                                                    $$\   $$ |
                                                                              \$$$$$$  |                                                                    \$$$$$$  |
                                                                               \______/                                                                      \______/ 

</pre> </div>
`;
document.getElementById("login").innerHTML += custom_text_header
