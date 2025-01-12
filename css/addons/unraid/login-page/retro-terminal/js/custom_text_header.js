
 //Custom Text Header //
 // ACSII slant font

// Needs to be inside <section id="login" class="shadow">
// YOU MUST ESCAPE ANY SINGLE BACKSLASHES LIKE SO: \\

let custom_text_header = `
<div class="custom-text-header"> <pre>
  ______       _                _    ______                       _                           _               
 |  ____|     | |              | |  |  ____|                     (_)                         (_)              
 | |__    ___ | | __ ___  _ __ | |_ | |__    _ __    __ _  _ __   _  _ __    ___   ___  _ __  _  _ __    __ _ 
 |  __|  / __|| |/ // _ \| '__|| __||  __|  | '_ \  / _` || '_ \ | || '_ \  / _ \ / _ \| '__|| || '_ \  / _` |
 | |____| (__ |   <|  __/| |   | |_ | |____ | | | || (_| || | | || || | | ||  __/|  __/| |   | || | | || (_| |
 |______|\___||_|\_\\___||_|    \__||______||_| |_| \__, ||_| |_||_||_| |_| \___| \___||_|   |_||_| |_| \__, |
                                                     __/ |                                               __/ |
                                                   |___/                                               |___/ 
</pre> </div>
`;
document.getElementById("login").innerHTML += custom_text_header
