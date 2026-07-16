<template>
    <v-slider
            :model-value="value"
            @update:modelValue="throttledSetValue"
            :max="max"
            :step="step"
            :hide-details="hideDetails" />
</template>

<script>
    module.exports = {
        props: ['value', 'wait', 'max', 'step', 'hideDetails'],
        created() {
            this.throttledSetValue = _.throttle(
                (v) => { this.$emit('update:value', v); },
                this.wait);
        },
    }
</script>
