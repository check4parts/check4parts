<script lang="ts">
  let { lable, type = "text", name, placeholder, required = false, value = $bindable() } : {
    lable: string;
    type?: string;
    name: string;
    placeholder: string;
    required?: boolean;
    value?: string;
  } = $props();
</script>

<label class="label">
  <span class="text-sm">{lable}</span>
  <input
    class="input focus:outline-primary-500 focus:outline-2 h-12 bg-white placeholder:text-gray-400"
    style="box-shadow: none;"
    {name}
    {type}
    {placeholder}
    {required}
    bind:value={value}
  />
</label>