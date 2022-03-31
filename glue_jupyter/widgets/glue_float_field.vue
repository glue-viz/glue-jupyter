<template>
    <v-text-field
            :label="label"
            :suffix="suffix"
            v-model="displayValue"
            type="number"
            :rules="[validNumber]"
            hide-details/>
</template>
<script>
    /* `displayValue` is linked to the text-field and `value` will only be updated when it's a valid number
       This means that any formatting such as '1e3' will be kept.
       Only when `value` is changed externally, `displayValue` will be update according to the current `value`.
    */
    module.exports = {
        props: ['value', 'label', 'suffix'],
        data: function() {
            return {
                // default value is the one that was intially passed
                displayValue: this.value
            }
        },
        methods: {
            validNumber() {
                // the strings returned are currently not displayed
                const value = Number(this.displayValue);
                if(this.displayValue.length === 0) {
                    return "Please enter a value"
                }
                if(isNaN(value)) { // invalid floats lead to a nan
                    return "Invalid number"
                }
                return true;
            }
        },
        watch: {
            displayValue() {
                // when we change the input, we only update value when valid
                if(this.validNumber() === true) { // invalid floats lead to a nan
                    // and we emit the change only when we have a valid number
                    const value = Number(this.displayValue);
                    this.$emit('update:value', value);
                }
            },
            value() {
                const currentValue = Number(this.displayValue);
                if((this.displayValue.length == 0) || isNaN(currentValue) || (currentValue !== this.value)) {
                    // externally, a change in value was triggered, that is not equal to the current value
                    // we now set displayValue, losing possible formatting
                    this.displayValue = this.value;
                }
            },
        },
    }
</script>
