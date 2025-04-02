import { AuthInvalidCredentialsError } from '@supabase/supabase-js';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
	depends('supabase:db:staff');
	const { data: staff } = await supabase
		.from('staff')
		.select('*,roles(name),trading_points(*)')
		.order('name');
	return { staff: staff ?? [] };
};
