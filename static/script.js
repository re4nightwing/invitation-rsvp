window.onload = function() {
  // Get the elements
  const weddingCard = document.querySelector('.wedding-card');
  const envelope = document.querySelector('.envelope');
  const envelopeTop = document.querySelector('.envelope-top');
  
  // Get the actual height of the wedding card after content loads
  const cardContentHeight = weddingCard.scrollHeight;
  
  // Start the animation after a delay (optional)
  setTimeout(() => {
      // Hide the envelope-top instantly
      
      // Animate the wedding card
      weddingCard.classList.add('animate');
      
      // Dynamically set the height to allow the transition to 'auto'
      weddingCard.style.height = `${cardContentHeight}px`;
      
      // Animate the envelope's top position
      envelope.classList.add('animate');
      envelopeTop.classList.add('animate');
    }, 500); // Adjust the delay as needed

    setTimeout(() => {
      goFullscreen();
    }, 2000);
};

function goFullscreen() {
  const weddingCard = document.querySelector('.wedding-card');
  const weddingCardImg = document.querySelector('.card-image');
  
  // Add the 'fullscreen' class to expand the card
  weddingCard.classList.add('fullscreen');
  //weddingCardImg.classList.add('fullscreen');
}