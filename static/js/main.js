document.addEventListener('DOMContentLoaded', function () {

  // --- Interactive star-rating picker -------------------------------
  // Replaces the plain <select> for ratings with clickable stars.
  // Falls back gracefully to the select if JS is disabled (progressive
  // enhancement) since the underlying <select> still submits the value.
  const ratingSelect = document.querySelector('select[name="rating"]');
  if (ratingSelect) {
    const wrapper = document.createElement('div');
    wrapper.className = 'star-picker mb-2';

    const stars = [];
    for (let i = 1; i <= 5; i++) {
      const star = document.createElement('span');
      star.textContent = '★';
      star.dataset.value = i;
      star.className = 'star-choice';
      wrapper.appendChild(star);
      stars.push(star);
    }

    function paint(value) {
      stars.forEach(function (s) {
        s.classList.toggle('star-filled', parseInt(s.dataset.value, 10) <= value);
      });
    }

    const initial = parseInt(ratingSelect.value, 10) || 0;
    paint(initial);

    wrapper.addEventListener('click', function (e) {
      if (!e.target.classList.contains('star-choice')) return;
      const value = parseInt(e.target.dataset.value, 10);
      ratingSelect.value = value;
      paint(value);
    });

    ratingSelect.style.display = 'none';
    ratingSelect.parentNode.insertBefore(wrapper, ratingSelect);
  }

  // --- Live client-side validation feedback --------------------------
  // Adds Bootstrap's is-valid/is-invalid classes as the person types,
  // instead of only finding out about a mistake after submitting.
  document.querySelectorAll('form').forEach(function (form) {
    const fields = form.querySelectorAll('input[required], textarea[required], input[type="email"]');
    fields.forEach(function (field) {
      field.addEventListener('input', function () {
        if (field.checkValidity()) {
          field.classList.remove('is-invalid');
          field.classList.add('is-valid');
        } else {
          field.classList.remove('is-valid');
          field.classList.add('is-invalid');
        }
      });
    });
  });

  // --- Booking date guard ---------------------------------------------
  // Prevents picking a date in the past on the booking form.
  const dateInput = document.querySelector('input[name="scheduled_date"]');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.setAttribute('min', today);
  }

});
