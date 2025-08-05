<script lang="ts">
	import { enhance } from '$app/forms';

	interface Props {
		staff: {
			id: string;
			user_id: string;
			email?: string;
			phone_number?: string;
			trading_point?: any;
			role: any;
		};
		emailConfirmToChange: boolean;
		tarading_points: any;
		roles: any;
		cardState?: 'view' | 'edit';
	}

	let { staff, cardState = $bindable('view'), tarading_points, roles, emailConfirmToChange = $bindable(false) }: Props = $props();

	let loading = $state(false);

	$effect(() => {
		cardState;
		loading = false;
	});
</script>

{#snippet row(
	title: string,
	value: string | undefined,
	name: string,
	type: 'select' | 'text',
	badge: boolean = false,
	select_data:
		| {
				value: string;
				label: string;
		  }[]
		| undefined = [],
	selected_id: string | undefined = ''
)}
	<div class="flex h-6 w-full items-center gap-4">
		<h4 class="text-surface-200 w-40 font-bold">{title}</h4>
		{#if cardState === 'view'}
			<p class={badge ? 'badge preset-filled-success-200-800' : 'text-primary-950-50'}>
				{value ? value : 'Не вказано'}
				{#if name === 'email' && emailConfirmToChange}
					<span class="badge preset-tonal-primary">зміну необхідно підтвердити</span>
				{/if}
			</p>
		{:else if type === 'text'}
			<input {type} {name} class="input w-80" {value} />
		{:else if type === 'select'}
			<select {name} class="select w-80" value={selected_id}>
				{#each select_data as option}
					<option value={option.value}>{option.label}</option>
				{/each}
			</select>
		{/if}
	</div>
{/snippet}

<section
	class="shadow-surface-50 mx-auto mt-6 rounded-xl p-8 shadow-[0px_0px_9px_17px_rgba(0,_0,_0,_0.1)]"
>
	<form
		method="POST"
		use:enhance={() => {
			return async ({ update }) => {
				update({ reset: false });
			};
		}}
		action="?/editContactInformation"
		onsubmit={() => (loading = true)}
	>
		<header class="mb-4 flex items-center justify-between rounded-xl">
			<h3 class="h5">Контактана інформація</h3>
			{#if cardState === 'view'}
				<button
					type="button"
					class="btn preset-outlined-primary-950-50 !border-2 font-bold"
					onclick={() => (cardState = 'edit')}>Редагувати</button
				>
			{:else if cardState === 'edit'}
				<div class="flex justify-end gap-4">
					<button
						type="button"
						class="btn preset-outlined-primary-950-50 !border-2 font-bold"
						onclick={() => (cardState = 'view')}>Скасувати</button
					>
					<button
						type="submit"
						class="btn preset-filled-primary-950-50 font-bold"
						disabled={loading}
						>{#if loading}
							Завантаження...
						{:else}
							Зберегти
						{/if}</button
					>
				</div>
			{/if}
		</header>
		<div class="flex flex-col gap-4">
			<input type="hidden" name="id" value={staff.id} />
			<input type="hidden" name="user_id" value={staff.user_id} />
			{@render row('Емейл', staff.email, 'email', 'text')}
			{@render row('Телефон', staff.phone_number, 'phone_number', 'text')}
			{@render row(
				'Торгова точка',
				staff.trading_point.name,
				'trading_point',
				'select',
				false,
				tarading_points.map((point: any) => ({
					value: point.id,
					label: `${point.name}`
				})),
				staff.trading_point.id
			)}
			{@render row(
				'Роль',
				staff.role.name,
				'role',
				'select',
				true,
				roles.map((role: any) => ({
					value: role.id,
					label: role.name
				})),
				staff.role.id
			)}
		</div>
	</form>
</section>
