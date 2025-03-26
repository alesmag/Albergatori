/* Importo Swiper come modulo */
import Swiper from 'https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.mjs'

/* Inizializzo una nuova istanza dell'oggetto Swiper 

Parametri del dizionario:
- slidesPerView: numero di slide mostrate pew pagina
- slidesPerGroup: numero di slide raggruppate durante la navigazione
- spaceBetween: spaziatura tra le slides 

- pagination: visualizza la navigazione dell'utente tramite bullets 
- navigation: serve per configurare i bottoni per la navigazione */
const swiper = new Swiper('.swiper', {

    slidesPerView: 4,
    slidesPerGroup: 4,
    spaceBetween: 5,

    pagination: {
        el: '.swiper-pagination',
    },

    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    }

})
