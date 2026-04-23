import ipyvuetify as v
import traitlets


class GlueFloatField(v.VuetifyTemplate):
    # template_file = (__file__, 'glue_float_field.vue')

    template = traitlets.Unicode("""
        <glue-float-field
            :label="label"
            :value.sync="value"
        />
    """).tag(sync=True)

    label = traitlets.Unicode().tag(sync=True)
    value = traitlets.Float().tag(sync=True)

    def __init__(self, label, initial_value):
        super().__init__()

        self.label = label
        self.value = float(initial_value)
