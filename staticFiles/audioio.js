// Flask-SocketIO connection to Heroku web server
var socket = io.connect('wss://caseai-e4620cbfb447.herokuapp.com/');
// using web audio API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
const audioContext = new AudioContext();

document.addEventListener('DOMContentLoaded', function () {
    // Log messages from the server
    const logDisplay = document.getElementById('log-display');
    socket.on('log', (data) => {
      console.log(data); // Replace with your code to show the log message to the user
      logDisplay.textContent = data.log;
    });
    const audioPlayer = document.getElementById('audio-player');
    //TODO - add event listener to INPUT audio from client

    // Test Output Button
    document.getElementById('testOutputButton').addEventListener('click', function() {
        fetch('/test_audio_output')
            fetch('/welcome.mp3')
                .then(response => response.blob())
                .then(blob => {
                    const objectURL = URL.createObjectURL(blob);
                    audioPlayer.src = objectURL;
                })
                .catch(error => console.error('Error fetching audio file:', error))

                
            .then(response => response.json())
            .then(data => {
            document.getElementById('resultMessage').textContent = data.message;
            })
            .catch(error => {
            console.error('Error:', error);
            });
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
});