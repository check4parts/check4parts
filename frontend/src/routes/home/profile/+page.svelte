<script lang="ts">
	import toast from 'svelte-french-toast';
	import EditNameModal from './(components)/EditNameModal.svelte';
	import ContacInformationCard from './(components)/ContacInformationCard.svelte';
	import SafetyCard from './(components)/SafetyCard.svelte';

	let { data, form } = $props();
	let { user, staff, points, roles } = $derived(data);

	let editNameOpenState = $state(false);
	let contactsCardState = $state<'view' | 'edit'>('view');

	let emailToConfirm = $derived(!!form?.email_sent);

	$effect(() => {
		if (form) {
			if (form?.success) {
				if (form?.message === 'name_updated') {
					editNameOpenState = false;
				}
				if (form?.message === 'contacts_updated') {
					contactsCardState = 'view';
				}
				if (emailToConfirm) {
					toast.success('Пітдвердіть дію на пошті', {
						duration: 5000
					});
				}
				toast.success('Дані успішно оновлені', {});
			} else {
				toast.error('Помилка при оновленні даних', {});
			}
		}
	});
</script>

<EditNameModal
	bind:openState={editNameOpenState}
	id={staff.id}
	data={{
		first_name: staff.first_name,
		last_name: staff.last_name,
		middle_name: staff.middle_name
	}}
/>

<section class="mx-auto h-full w-[95%]">
	<div class="grid grid-cols-[auto_1fr] grid-rows-2 items-center gap-4">
		<div class="row-span-2 flex h-40 w-40 items-center justify-center p-2">
			<img src="/avatar.svg" alt="Аватар" class="h-full w-full object-contain" />
		</div>
		<div class="flex items-center gap-2">
			<h2 class="self-end text-2xl font-medium text-gray-800">
				{staff.last_name}
				{staff.first_name}
				{staff.middle_name}
			</h2>
			<button type="button" class="btn-icon size-7 p-0" onclick={() => (editNameOpenState = true)}>
				<img class="size-7" src="/edit-button-icon.svg" alt="edit" width="28" height="28" />
			</button>
		</div>
	</div>
	<ContacInformationCard
		staff={{
			id: staff.id,
			user_id: staff.user_id,
			email: user?.email,
			phone_number: staff.phone_number,
			trading_point: staff.trading_points,
			role: staff.roles
		}}
		bind:cardState={contactsCardState}
		tarading_points={points}
		{roles}
		emailConfirmToChange={emailToConfirm}
	/>
	<SafetyCard last_login={user?.last_sign_in_at} bind:form />
</section>
