let intro = document.querySelector('.intro');
let logoSpan = document.querySelectorAll('.logo');
let logoheader = document.querySelector('.logo-header');

window.addEventListener('DOMContentLoaded', () => {
    intro.classList.add('show');
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
})