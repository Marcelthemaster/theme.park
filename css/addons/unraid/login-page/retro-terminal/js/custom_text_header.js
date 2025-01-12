
 //Custom Text Header //
 // ACSII slant font

// Needs to be inside <section id="login" class="shadow">
// YOU MUST ESCAPE ANY SINGLE BACKSLASHES LIKE SO: \\

let custom_text_header = `
<div class="custom-text-header"> <pre>
    ______     __             __  ______            _                      _            
   / _________/ /_____  _____/ /_/ ________  ____ _(_____  ___  ___  _____(_____  ____ _
  / __/ / ___/ //_/ _ \/ ___/ __/ __/ / __ \/ __ `/ / __ \/ _ \/ _ \/ ___/ / __ \/ __ `/
 / /___/ /__/ ,< /  __/ /  / /_/ /___/ / / / /_/ / / / / /  __/  __/ /  / / / / / /_/ / 
/_____/\___/_/|_|\___/_/   \__/_____/_/ /_/\__, /_/_/ /_/\___/\___/_/  /_/_/ /_/\__, /  
                                          /____/                               /____/   
</pre> </div>
`;
document.getElementById("login").innerHTML += custom_text_header
