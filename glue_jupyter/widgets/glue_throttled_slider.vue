<template>
    <v-slider
            :value="value"
            @input="throttledSetValue"
            :max="max"
            :step="step"
            :hide="hideDetails" />
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
