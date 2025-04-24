import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
	depends('supabase:db:providers');
	const { data: suppliers } = await supabase.from('providers').select('*');

	const { data: added_suppliers } = await supabase
		.from('company_provider')
		.select('*,providers(*)');

	return { suppliers: suppliers ?? [], added_suppliers: added_suppliers ?? [] };
};

export const actions = {
	add: async ({ request, locals: { supabase } }) => {
		const formData = await request.formData();
		const supplier_id = formData.get('supplier_id')?.toString();
		const data_props = JSON.parse(formData.get('data_props')?.toString() || '{}');
		const entries = Array.from(
			formData.entries().filter(([key]) => key !== 'supplier_id' && key !== 'data_props')
		);
		const accessData = Object.fromEntries(entries);
		console.log('accessData', accessData, formData);

		const { data, error } = await supabase
			.from('company_provider')
			.insert([{ provider_id: supplier_id, access_data: accessData, data: data_props }])
			.select();

		console.log(data, error);

		if (error) {
			return { success: false, message: error.message };
		} else {
			return { success: true, message: 'added' };
		}
	}
};
