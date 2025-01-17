<template>
  <div class="custom-message error">
    Diese Fahrt fällt aus!
  </div>
</template>

<style scoped>
.custom-message {
  display: flex;
  align-items: center;
  margin-top: 0.5rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  color: #dc2625;
  background-color: #fef3f3;
  border-radius: 4px;
  border: solid 1px #fecaca;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
  line-height: 1.2;
  max-width: fit-content;
}
</style>