document.addEventListener('DOMContentLoaded', function () {
    const profileIcon = document.getElementById('profileIcon');
    const profilePopup = document.getElementById('profilePopup');
    const closeBtn = profilePopup.querySelector('.close');

    const userNameEl = document.getElementById('user-name');
    const userInfoEl = document.getElementById('user-info');
    const progressValueEl = document.getElementById('progress-value');
    const coursesValueEl = document.getElementById('courses-value');
    const ratingValueEl = document.getElementById('rating-value');

    // Simulating logged-in user ID (replace with actual logic for logged-in user)
    const loggedInUserId = 1; // Replace with dynamic user ID if available

    // Function to fetch user profile from backend API
    async function fetchUserProfile(userId) {
        try {
            const response = await fetch('/profile', {
                method: 'POST', // Use POST instead of GET
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ userId: userId }) // Pass userId if needed
            });
            const data = await response.json();
            if (data.error) {
                console.error('User not found');
                return;
            }
    
            // Update profile with fetched data
            userNameEl.textContent = data.name;
            userInfoEl.textContent = data.role;
            progressValueEl.textContent = 12;
            coursesValueEl.textContent = data.courses;
            ratingValueEl.textContent = data.rating;
            console.log(data);
        } catch (error) {
            console.error('Error fetching user profile:', error);
        }
    }

    // Show profile popup
    profileIcon.addEventListener('click', function (e) {
        e.preventDefault();
        profilePopup.style.display = 'block';
        fetchUserProfile(loggedInUserId); // Fetch profile when opening the popup
    });

    // Close profile popup
    closeBtn.addEventListener('click', function () {
        profilePopup.style.display = 'none';
    });

    // Close profile popup if clicking outside of it
    window.addEventListener('click', function (e) {
        if (e.target === profilePopup) {
            profilePopup.style.display = 'none';
        }
    });
});