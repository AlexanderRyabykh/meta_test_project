var vue = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        therapists: ''
    },
    mounted() {
        axios
            //.get('https://jsonplaceholder.typicode.com/photos')
            .get('http://localhost:5000/get-main-data')
            .then(response => this.therapists = response.data);
    }
})