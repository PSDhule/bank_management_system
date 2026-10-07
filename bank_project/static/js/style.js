document.addEventListener("DOMContentLoaded", function () { 

    const menuToggle = document.getElementById ("menuToggle"); 
    const navLinks = document.getElementById("navLinks");

    if (!menuToggle || !navLinks) {
        return;
    }
    
    menuToggle.addEventListener("click", function () { 
        navLinks.classList.toggle("show"); 
        
        const icon = menuToggle.querySelector("i"); 
        
        if (navLinks.classList.contains("show")) { 
            
            icon.classList.remove("fa-bars"); 
            icon.classList.add("fa-xmark"); 
            
            } else { 
                
                icon.classList.remove("fa-xmark"); 
                icon.classList.add("fa-bars"); 
            } 
            
    }); 

    const navItems = navLinks.querySelectorAll("a");

    navItems.forEach(function (item) {
        item.addEventListener("click", function () {

            if (window.innerWidth <= 768) {

                navLinks.classList.remove("show");

                const icon = menuToggle.querySelector("i");

                icon.classList.remove("fa-xmark");

                icon.classList.add("fa-bars");
            }
        });
        
    });

});
