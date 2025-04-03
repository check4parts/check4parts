<script lang="ts">
  let { lable, name, placeholder, required = false, value = $bindable() } : {
    lable: string;
    name: string;
    placeholder: string;
    required?: boolean;
    value?: string;
    showPassword?: boolean
  } = $props();

  let showPassword = $state(false);
  $inspect(showPassword);

  const togglePassword = () => {
    showPassword = !showPassword
  }
</script>

<label class="relative block w-full label">
  <span class="text-sm">{lable}</span>
  <input
    class="input focus:outline-primary-500 h-12 px-4 py-3 pr-14 bg-white placeholder:text-gray-400"
    style="box-shadow: none;"
    {name}
    type={showPassword ? 'text' : 'password'}
    {placeholder}
    {required}
    {value}
  />
  <button type="button" class="absolute top-[43%] right-4" onmousedown={togglePassword}>
    {#if showPassword}
    <img src="/hide-pass.svg" alt="search" class="size-8"  />
    {:else}
    <img src="/show-pass.svg" alt="search" class="size-8" />
    {/if}
  </button>
</label>