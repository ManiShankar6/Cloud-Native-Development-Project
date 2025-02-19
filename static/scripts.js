const { motion } = window['framer-motion']; 

// React Component for Heading Animation with Circle
function HeadingAnimation() {
    return (
        React.createElement('div', { className: 'heading-container', style: { display: 'flex', alignItems: 'center' } },
            React.createElement('div', {
                className: 'circle',
                style: { width: '100px', height: '100px', borderRadius: '50%', overflow: 'hidden', marginRight: '15px' }
            },
                React.createElement('video', {
                    autoPlay: true,
                    loop: true,
                    muted: true,
                    style: { width: '100%', height: '100%', objectFit: 'cover' }
                },
                    React.createElement('source', { src: '/files/vid2.mp4', type: 'video/mp4' }),
                    "Your browser does not support the video tag."
                )
            ),
            React.createElement(motion.div, { className: 'text', style: { textAlign: 'center', color: 'white' } },
                React.createElement(motion.h1, {
                    style: {
                        fontSize: '3rem',
                        color: '#FFD700',
                        fontWeight: 'bold',
                        textShadow: '1px 1px 5px rgba(255, 215, 0, 0.8)',
                        margin: '0'
                    },
                    initial: { y: -50, opacity: 0 },
                    animate: { y: 0, opacity: 1 },
                    whileHover: { scale: 1.1, textShadow: '0px 0px 10px rgba(255, 255, 0, 1)' },
                    transition: { duration: 0.8 }
                }, "Imagery"),
                React.createElement(motion.h2, {
                    style: {
                        fontSize: '1.5rem',
                        color: '#e0e0e0',
                        margin: '0'
                    },
                    initial: { y: 50, opacity: 0 },
                    animate: { y: 0, opacity: 1 },
                    whileHover: { scale: 1.05, color: '#FFD700' },
                    transition: { duration: 0.8 }
                }, "A platform where your images shine with elegance!")
            )
        )
    );
}

// Render the Heading Animation
document.addEventListener('DOMContentLoaded', () => {
    const headingContainer = document.getElementById('heading-animation');
    if (headingContainer) {
        ReactDOM.render(React.createElement(HeadingAnimation), headingContainer);
    }

    // Attach Event Listener to File Input
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            updateFileNames(this);
        });
    }

    document.querySelectorAll(".image-card").forEach((card) => {
        const imageName = card.querySelector(".thumbnail").dataset.image;
        const metadataContainer = card.querySelector(".metadata");
        const titleElement = metadataContainer.querySelector("h3");
    
        fetch(`/files/${imageName.split('.').slice(0, -1).join('.')}.json`)
            .then(response => {
                if (!response.ok) throw new Error("Metadata not found");
                return response.json();
            })
            .then(data => {
                titleElement.innerText = data.title; // Set the title
                metadataContainer.dataset.description = data.description; // Store the description
            })
            .catch(error => {
                console.log(`Metadata not found for ${imageName}:`, error);
            });
    });
    
});

// Function to Update Selected File Names
function updateFileNames(input) {
    const fileNames = Array.from(input.files).map(file => file.name).join(", ");
    const fileNamesDisplay = document.getElementById('file-names');

    if (fileNamesDisplay) {
        fileNamesDisplay.textContent = fileNames || "No files selected";
    }
}

// Open full-screen modal


function openFullscreen(src, title, description) {
    const modal = document.getElementById('fullscreenModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalImage = document.getElementById('modalImage');
    const modalDescription = document.getElementById('modalDescription');
    const modalContentContainer = document.querySelector('.modal-content-container');

    modal.style.display = 'flex';
    modalTitle.innerText = title; // Display title
    modalImage.src = src;
    modalImage.style.maxHeight = "70vh";
    modalImage.style.objectFit = "contain";
    
    // Preserve HTML formatting for the description
    modalDescription.innerHTML = `<strong>Description:</strong> ${description}`;

    // Reset scroll position to top when opening a new image
    modalContentContainer.scrollTop = 0;
}


// Close full-screen modal
function closeFullscreen() {
    const modal = document.getElementById('fullscreenModal');
    modal.style.display = 'none';
}
