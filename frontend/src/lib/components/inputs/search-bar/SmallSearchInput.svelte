<script lang="ts">
    type Props = {
        value?: string;
        placeholder?: string;
        iconSrc?: string;
        class?: string;
        inputClass?: string;
        disabled?: boolean;
        name?: string;
        id?: string;
    };

    let {
        value = $bindable(''),
        placeholder = 'Пошук...',
        iconSrc = '/search-icon.svg',
        class: containerClass = '',
        inputClass = '',
        disabled = false,
        name = 'search',
        id = 'search'
    }: Props = $props();
</script>

<label class="mx-1 relative block focus-within:text-gray-500 {containerClass}">
    <img 
        src={iconSrc} 
        alt="search" 
        class="absolute left-4 top-1/2 size-6 -translate-y-1/2 pointer-events-none" 
    />
    <input
        type="text"
        {name}
        {id}
        {disabled}
        bind:value
        {placeholder}
        class="appearance-none rounded-lg px-4 pl-14 placeholder:text-sm focus:outline-none {inputClass} text-ellipsis"
    />
</label>
