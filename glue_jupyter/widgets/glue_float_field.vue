<template>
    <v-text-field
            :label="label"
            :suffix="suffix"
            v-model.number="value"
            type="number"
            :rules="[(v) => v !== '']"
            hide-details/>
</template>
<script>
    module.exports = {
        props: ['value', 'label', 'suffix'],
        watch: {
            value(v) {
                if (v !== '') {
                    this.$emit('update:value', v);
                }
            }
        },
    }
</script>
