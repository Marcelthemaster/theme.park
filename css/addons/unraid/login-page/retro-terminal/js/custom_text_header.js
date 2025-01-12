
 //Custom Text Header //
 // ACSII slant font

// Needs to be inside <section id="login" class="shadow">
// YOU MUST ESCAPE ANY SINGLE BACKSLASHES LIKE SO: \\

let custom_text_header = `
<div class="custom-text-header"> <pre>
  __|       |             |    __|              _)                       _)              
  _|    _|  | /   -_)   _| _|  _|     \    _` |  |    \    -_)   -_)   _| |    \    _` | 
 ___| \__| _\_\ \___| _| \__| ___| _| _| \__, | _| _| _| \___| \___| _|  _| _| _| \__, | 
                                         ____/                                    ____/                                            
</pre> </div>
`;
document.getElementById("login").innerHTML += custom_text_header
