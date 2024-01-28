<!-- The arrow for marking the current instruction in TOY -->
<template>
    <span class="toy-current-cycle text-light bg-dark">
        <slot></slot>
        <i class="bi bi-caret-right-fill"></i>
    </span>
</template>

<style scoped>
.toy-current-cycle {
    padding: 0em 0.2em;
    border-radius: 0.3em;
    float: left;
}
</style>
