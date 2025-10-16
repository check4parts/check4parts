<script lang="ts">
    import { goto, preloadData } from '$app/navigation';
    import { page } from '$app/state';
    import toast from 'svelte-french-toast';
    import ClientTypeSelect from './(components)/ClientTypeSelect.svelte';
    import SmallSearchInput from '$lib/components/inputs/search-bar/SmallSearchInput.svelte';
	import { stringFromBase64URL } from '@supabase/ssr';

    let { data } = $props();
    let { clients, clientTypes } = $derived(data);

    let selectedTypeIds = $state<string[]>([]);
    let search = $state<string>('');

    function normalizeText(text: string): string {
        return text
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    let filteredClients = $derived.by(() => {
        let result = clients;

        if (selectedTypeIds.length > 0) {
            result = result.filter((client) => selectedTypeIds.includes(client.type_id));
        }

        if (search.trim()) {
            const normalizedSearch = normalizeText(search);
            
            result = result.filter((client) => {
                const fullName = normalizeText(
                    `${client.last_name || ''} ${client.first_name || ''} ${client.middle_name || ''}`
                );                
                const phoneNumber = normalizeText(client.phone_number || '');
                const note = normalizeText(client.note || '');
                const carNumbers = normalizeText(client.cars?.map((car: { license_plate: string; }) => car.license_plate).join(' '));

                return (
                    fullName.includes(normalizedSearch) ||
                    phoneNumber.includes(normalizedSearch) ||
                    note.includes(normalizedSearch) ||
                    carNumbers.includes(normalizedSearch)
                );
            });
        }

        return result;
    });

    $inspect(filteredClients);

    const isSuccess = page.url.searchParams.has('success');
    $effect(() => {
        if (isSuccess) {
            toast.success('Клієнт успішно додано');
            goto('/home/clients', { replaceState: true, noScroll: true, keepFocus: true });
        }
    });
</script>

{#snippet noClientsMessage()}
    {#if clients.length === 0}
        <div class="flex h-full w-full flex-col items-center justify-center">
            <h3 class="h5">Тут поки що порожньо.</h3>
            <p>Додайте першого клієнта, щоб розпочати роботу.</p>
        </div>
    {:else}
        <div class="flex h-full w-full flex-col items-center justify-center">
            <h3 class="h5">Клієнти не знайдені.</h3>
            <p>Спробуйте змінити фільтри пошуку.</p>
        </div>
    {/if}
{/snippet}

<main class="grid h-full grid-rows-[auto_auto_1fr] gap-2">
    <header class="flex items-center justify-between">
        <h2 class="h3">Клієнти</h2>
        <a class="btn preset-filled-primary-950-50" href="/home/clients/add">Додати клієнта</a>
    </header>

    <section class="flex items-center justify-between">
        <ClientTypeSelect
            items={clientTypes}
            bind:selectedIds={selectedTypeIds}
            label="Тип клієнта"
        />
        <SmallSearchInput
            bind:value={search}
            placeholder="Пошук за ПІБ, номером телефону, приміткою та номером авто"
        />
    </section>
    
    <section class="overflow-hidden flex flex-col">
        {#if filteredClients.length > 0}
            <div class="border-primary-950 overflow-hidden rounded-xl border-2">
                <div class="h-full overflow-y-auto">
                    <table class="table min-w-full border-collapse">
                        <thead class="bg-primary-950 sticky top-0 z-10">
                            <tr class="text-primary-50">
                                <th>ПІБ</th>
                                <th>Номер телефону</th>
                                <th>Примітка</th>
                            </tr>
                        </thead>
                        <tbody class="!divide-primary-950 !divide-y-2">
                            {#each filteredClients as client (client.id)}
                                {#if client.phone_number !== ''}
                                    <tr
                                        onmousemove={() => preloadData('/home/clients/' + client.id)}
                                        onclick={() => goto('/home/clients/' + client.id)}
                                        class="divide-primary-950 hover:bg-primary-50 group w-full divide-x-2"
                                        class:bg-amber-100={client.state === 'paused'}
                                    >
                                        <td>{client.last_name} {client.first_name} {client.middle_name}</td>
                                        <td>{client.phone_number}</td>
                                        <td>{client.note}</td>
                                    </tr>
                                {/if}
                            {/each}
                        </tbody>
                    </table>
                </div>
            </div>
        {:else}
            <section class="h-2/3">
                {@render noClientsMessage()}
            </section>
        {/if}
    </section>
</main>
