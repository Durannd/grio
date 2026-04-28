<div class="spinner-wrapper">
  <div class="spinner"></div>
</div>

<style>
  .spinner-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    padding: 2rem;
  }
  .spinner {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    border: 4px solid rgba(255, 255, 255, 0.2);
    border-top-color: #ffffff;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
