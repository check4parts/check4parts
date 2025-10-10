<script lang="ts">
    interface ItemData {
        label: string;
        value: string;
        disabled?: boolean;
    }

    interface Props {
        items: ItemData[];
        name: string;
        value?: string;
        required?: boolean;
        missing?: boolean;
        initialValue?: string;
        disabled?: boolean;
        orientation?: 'vertical' | 'horizontal';
    }

    let {
        items,
        name,
        value = $bindable(),
        required = false,
        missing = false,
        initialValue,
        disabled = false,
        orientation = 'vertical'
    }: Props = $props();

    let selectedValue = $state<string>(initialValue || '');

    $effect(() => {
        value = selectedValue;
    });
</script>

<div class="flex flex-col gap-2">
    <div class="flex {orientation === 'vertical' ? 'flex-col' : 'flex-row'} gap-4">
        {#each items as item}
            <div class="flex items-center space-x-2">
                <input
                    type="radio"
                    id="{name}-{item.value}"
                    {name}
                    value={item.value}
                    bind:group={selectedValue}
                    disabled={disabled || item.disabled}
                    {required}
                    class="size-5 cursor-pointer accent-primary-950 disabled:cursor-not-allowed disabled:opacity-50"
                />
                <label
                    for="{name}-{item.value}"
                    class="cursor-pointer text-sm {disabled || item.disabled ? 'opacity-50 cursor-not-allowed' : ''} {missing && !value ? 'text-error-400' : ''}"
                >
                    {item.label}
                </label>
            </div>
        {/each}
    </div>
</div>
