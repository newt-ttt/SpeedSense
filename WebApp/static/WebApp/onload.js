let intro = document.querySelector('.intro');
let logoSpan = document.querySelectorAll('.logo');


window.addEventListener('DOMContentLoaded', () => {
    // Check if localStorage is available (IE8+) and make sure that the visited flag is not already set.
    if(typeof window.localStorage !== "undefined" && !localStorage.getItem('visited')) {
         // Set visited flag in local storage
         localStorage.setItem('visited', true); 
         intro.classList.add('hide');
         
    } else {
        
            setTimeout(() => {

                logoSpan.forEach((span, idx) => {
                    setTimeout(() => {
                        span.classList.add('active');
                    }, (idx + 1) * 400)
                });

                setTimeout(() => {
                    logoSpan.forEach((span, idx) => {

                        setTimeout(() => {
                            span.classList.remove('active');
                            span.classList.add('fade');
                        }, (idx + 1) * 50)
                    })
                }, 2000);

                setTimeout(() => {
                    intro.style.top = "-100vh"
                }, 2300)

            })
        }
    })
