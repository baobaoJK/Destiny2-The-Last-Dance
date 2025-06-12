<script lang="ts" setup>
import { defineProps } from 'vue'

defineProps({
  showInfoBoard: Boolean,
  type: String
})
</script>

<template>
  <div
    id="info"
    :class="{
      hide: !showInfoBoard,
      show: showInfoBoard,
      right: type === 'right',
      left: type === 'left'
    }"
  >
    <slot name="close-button"></slot>
    <slot name="title"></slot>
    <slot name="content"></slot>
  </div>
</template>

<style lang="scss">
$borderColor: #2b3037;

@keyframes showInfoRight {
  0% {
    transform: translateX(100%);
  }

  100% {
    transform: translateX(0%);
  }
}

@keyframes showInfoLeft {
  0% {
    transform: translateX(-100%);
  }

  100% {
    transform: translateX(0%);
  }
}

#info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 6.25rem;
  width: 30rem;
  height: calc(100vh - 6.25rem);
  padding: 2rem;
  box-sizing: border-box;
  background-color: #262b31;
  transition: transform 1s;

  .close-button {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: absolute;
    top: calc(50% - 20rem);
    width: 3rem;
    height: 40rem;
    color: white;
    font-size: 1.5rem;
    font-weight: bold;
    box-sizing: border-box;
    background-color: #262b31;
    text-align: center;

    a {
      cursor: pointer;
      transition: opacity 0.5s;
      writing-mode: vertical-rl;

      &:hover {
        opacity: 0.5;
      }
    }
  }

  h1 {
    font-size: 2rem;
    letter-spacing: 1rem;
    margin-bottom: 2rem;
  }

  h2 {
    font-size: 1.75 rem;
    letter-spacing: 0.5rem;
    margin-bottom: 0.5rem;
  }

  p {
    font-size: 1rem;
    margin-bottom: 0.25rem;
  }

  hr {
    margin: 1rem 0;
  }
}

.right {
  right: 0;
  border-left: 0.25rem solid $borderColor;

  &.show {
    animation: showInfoRight 1s ease-in-out;
  }

  &.hide {
    transform: translateX(100%);
  }

  .close-button {
    left: -3rem;
    border-right: 0.25rem solid $borderColor;
    clip-path: polygon(0% 15%, 100% 0, 100% 100%, 100% 100%, 0 85%);
  }
}

.left {
  left: 0;
  border-right: 0.25rem solid $borderColor;

  &.show {
    animation: showInfoLeft 1s ease-in-out;
  }

  &.hide {
    transform: translateX(-100%);
  }

  .close-button {
    right: -3rem;
    border-left: 0.25rem solid $borderColor;
    clip-path: polygon(0 0, 0% 0, 100% 15%, 100% 85%, 0 100%);
  }
}
</style>
