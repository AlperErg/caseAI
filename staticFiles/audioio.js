// Flask-SocketIO connection to Heroku web server
var socket = io.connect('wss://caseai-e4620cbfb447.herokuapp.com/');
// using web audio API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
const audioContext = new AudioContext();

document.addEventListener('DOMContentLoaded', function () {
    const audioPlayer = document.getElementById('audio-player');
    //TODO - add event listener to INPUT audio from client

    // Test Output Button
    document.getElementById('testOutputButton').addEventListener('click', function() {
        fetch('/welcome.mp3')
          .then(response => response.blob())
          .then(blob => {
              const objectURL = URL.createObjectURL(blob);
              audioPlayer.src = objectURL;
          })
          .catch(error => console.error('Error fetching audio file:', error))
    });
    // Start Talk Button
    document.getElementById('executeButton').addEventListener('click', function() {
        // Ask for microphone permissions
        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(() => {
            // Send a request to the Flask endpoint
            fetch('/run_python_code')
              .then(response => response.json())
              .then(data => {
                document.getElementById('resultMessage').textContent = data.message;
              })
              .catch(error => {
                console.error('Error:', error);
              });
          })
          .catch(error => {
            console.error('Error accessing microphone:', error);
          });
    });

    // Log messages from the server
    const resultMessage = document.getElementById('resultMessage');

    socket.on('message', function(data) {
        resultMessage.textContent = data.message;
    });     
});