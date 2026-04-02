<template>
  <footer class="landing-footer">
    <div class="container footer-content">
      <div class="row gy-5">
        <div class="col-lg-6 d-flex flex-column justify-content-between">
          <div>
            <div class="footer-brand mb-3">LaunchPad</div>
            <p class="footer-tagline">
              Next-Gen Campus Recruitment.
            </p>
          </div>
        </div>
        
        <!-- Roles -->
        <div class="col-lg-6 d-flex justify-content-lg-end">
          <div>
            <h4 class="footer-heading">Roles</h4>
            <ul class="footer-links">
              <li><router-link to="/register?role=student">Students</router-link></li>
              <li><router-link to="/register?role=company">Companies</router-link></li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom mt-5 pt-4 border-top">
        <div class="row">
          <div class="col-12 text-center text-md-start">
            <p class="copyright mb-0">&copy; {{ new Date().getFullYear() }} LaunchPad.</p>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.landing-footer {
  background-color: var(--color-primary, #0D0D12);
  border-radius: 4rem 4rem 0 0;
  padding: 6rem 0 3rem;
  margin-top: -2rem;
  position: relative;
  z-index: 10;
  box-shadow: 0 -20px 40px rgba(0, 0, 0, 0.3);
}

.footer-brand {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 1.5rem;
  color: var(--color-text-light);
  letter-spacing: -0.02em;
}

.footer-tagline {
  font-family: var(--font-heading);
  font-size: 1rem;
  color: #B4B4BC;
  line-height: 1.6;
}

.footer-heading {
  font-family: var(--font-heading);
  font-weight: 600;
  font-size: 1rem;
  color: var(--color-text-light);
  margin-bottom: 1.5rem;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.footer-links a {
  font-family: var(--font-heading);
  color: #B4B4BC;
  font-size: 0.875rem;
  text-decoration: none;
  transition: color 0.2s, transform 0.2s;
  display: inline-block;
}

.footer-links a:hover {
  color: var(--color-accent);
  transform: translateX(4px);
}

.border-top {
  border-top: 1px solid rgba(250, 248, 245, 0.05) !important;
}

.copyright {
  font-family: var(--font-heading);
  font-size: 0.875rem;
  color: #B4B4BC;
}
</style>
