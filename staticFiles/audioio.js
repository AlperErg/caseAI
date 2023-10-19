// Flask-SocketIO connection to Heroku web server
var socket = io.connect('wss://caseai-e4620cbfb447.herokuapp.com/');
// using web audio API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
const audioContext = new AudioContext();

document.addEventListener('DOMContentLoaded', function () {
    const audioPlayer = document.getElementById('audio-player');
    fetch('/welcome.mp3')
        .then(response => response.blob())
        .then(blob => {
            const objectURL = URL.createObjectURL(blob);
            audioPlayer.src = objectURL;
        })
        .catch(error => console.error('Error fetching audio file:', error))
    // WebSocket event listener to OUTPUT audio to client
    socket.on('audio_output', function (audioOutput) {
        try {
            // get the audio element
            const audioElement = document.querySelector("audio");

            // pass it into the audio context
            const track = audioContext.createMediaElementSource(audioElement);
        } catch (error) {
            console.error('Error playing sound:', error);
        }
    });
    //TODO - add event listener to INPUT audio from client

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
      // Test Output Button
      document.getElementById('testOutputButton').addEventListener('click', function() {
          fetch('/test_audio_output')
            .then(response => response.json())
            .then(data => {
              document.getElementById('resultMessage').textContent = data.message;
            })
            .catch(error => {
              console.error('Error:', error);
            });
      });
      socket.on('log', function(data) {
          console.log('Received log message:', data.message);
          $('#log').append('<p>' + data.message + '</p>');
      });          
});